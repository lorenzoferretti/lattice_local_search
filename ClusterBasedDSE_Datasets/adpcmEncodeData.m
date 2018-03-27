function [data, featureSets, discretizedFeatureSets] = adpcmEncodeData(path,resize)
% This function extract data from the adpcm_encode database and prepare data 
% for the exploration. In a online exploration scenario, data will not 
% contain area and latency informations since these will be obtained as
% result of the synthesis process.    
    
    conn = sqlite(which(strcat(path, '/adpcm_encode.db'),'readonly');
    adpcm_encode_data = fetch(conn,'SELECT * FROM adpcm_encode');
    adpcm_encode_data(:,1) = [];
    latencies = [adpcm_encode_data{:,1}];
    intervals = [adpcm_encode_data{:,2}];
    ffs = [adpcm_encode_data{:,3}];
    luts = [adpcm_encode_data{:,4}];
    main_loop = [adpcm_encode_data{:,5}];
    mac_loops = [adpcm_encode_data{:,6}];
    update_loops = [adpcm_encode_data{:,7}];
    encode_inline = [adpcm_encode_data{:,8}];
    help_loop = [adpcm_encode_data{:,9}];
    bundle_a = [adpcm_encode_data{:,10}];
    bundle_b = [adpcm_encode_data{:,11}];
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
    featureSets{3} = [0,2,11,22];
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
