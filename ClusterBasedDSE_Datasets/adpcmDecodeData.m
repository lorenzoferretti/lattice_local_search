function [data, featureSets, discretizedFeatureSets] = adpcmDecodeData(path, resize)
% This function extract data from the adpcm_decode database and prepare data 
% for the exploration. In a online exploration scenario, data will not 
% contain area and latency informations since these will be obtained as
% result of the synthesis process.        
    
    conn = sqlite(which(strcat(path, '/adpcm_decode.db')),'readonly');
    adpcm_decodeData = fetch(conn,'SELECT * FROM adpcm_decode');
    adpcm_decodeData(:,1) = [];
    latencies = [adpcm_decodeData{:,1}];
    intervals = [adpcm_decodeData{:,2}];
    ffs = [adpcm_decodeData{:,3}];
    luts = [adpcm_decodeData{:,4}];
    main_loop = [adpcm_decodeData{:,5}];
    mac_loops = [adpcm_decodeData{:,6}];
    update_loops = [adpcm_decodeData{:,7}];
    encode_inline = [adpcm_decodeData{:,8}];
    help_loop = [adpcm_decodeData{:,9}];
    bundle_a = [adpcm_decodeData{:,10}];
    bundle_b = [adpcm_decodeData{:,11}];
    data = [double(latencies).' double(intervals).' double(ffs).' double(luts).' double(main_loop).' double(mac_loops).' double(update_loops).' double(encode_inline).' double(help_loop).' double(bundle_a).' double(bundle_b).'];

    close(conn)

    clear conn;
    
    %% Clean unuseful data 
    % TODO: automate this process
    % Data has this format: latencies intervals ffs luts colums_loops row_loops accuracy_loops bundleA bundleB
    % Since bundleA never changes it is removed because it has zero standard
    % deviation, also intevals and luts are removed for testing.

    data(:,2) = [];
    data(:,3) = [];
    data(:,8)= [];

    % featureSets contains the information related to the daset.
    % For each feature we store in a list all the admissible values we want
    % to consider during the exploration
    featureSets = {};
    featureSets{1} = [0,5,10,25,50];
    featureSets{2} = [0,2,5,10];
    featureSets{3} = [0,2,5,10];
    featureSets{4} = [0,1];
    featureSets{5} = [0,6];
    featureSets{6} = [0,1];
    discretizedFeatureSets = discretizeSet(featureSets);

    dataCol = size(data,2);

    if resize
        data(:,3:dataCol) = discretizeFeature(featureSets,discretizedFeatureSets,data(:,3:dataCol));
        maxVal = max(data(:,1:2));
        data(:,1:2) = data(:,1:2)./maxVal;
    end

end
