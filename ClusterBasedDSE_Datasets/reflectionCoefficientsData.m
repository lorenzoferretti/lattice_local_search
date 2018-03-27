function [data, featureSets, discretizedFeatureSets] = reflectionCoefficientsData(path,resize)
% This function extract data from the Reflection_coefficients database and prepare data 
% for the exploration. In a online exploration scenario, data will not 
% contain area and latency informations since these will be obtained as
% result of the synthesis process.     

    conn = sqlite(which(strcat(path, '/Reflection_coefficients.db')),'readonly');
    reflectionCoeffData = fetch(conn,'SELECT * FROM Reflection_coefficients');
    reflectionCoeffData(:,1) = [];
    latency = [reflectionCoeffData{:,1}];
    ffs = [reflectionCoeffData{:,2}];
    luts = [reflectionCoeffData{:,3}];
    loop0 = [reflectionCoeffData{:,4}];
    loop1 = [reflectionCoeffData{:,5}];
    loop2 = [reflectionCoeffData{:,6}];
    loop3 = [reflectionCoeffData{:,7}];
    loop4 = [reflectionCoeffData{:,8}];
    inline_abs = [reflectionCoeffData{:,9}];
    inline_norm = [reflectionCoeffData{:,10}];
    inline_div = [reflectionCoeffData{:,11}];
    inline_add = [reflectionCoeffData{:,12}];
    inline_mult_r = [reflectionCoeffData{:,13}];
    bundle_a = [reflectionCoeffData{:,14}];
    bundle_b = [reflectionCoeffData{:,15}];
    data = [double(latency).' double(ffs).' double(luts).' double(loop0).' double(loop1).' double(loop2).' double(loop3).' double(loop4).' double(inline_abs).' double(inline_norm).' double(inline_div).' double(inline_add).' double(inline_mult_r).' double(bundle_a).' double(bundle_b).'];

    close(conn)

    clear conn;
    
    %% Clean unuseful data 
    % TODO: automate this process
    % Since bundleA never changes it is removed because it has zero standard
    % deviation, also intevals and luts are removed for testing.

    data(:,3) = [];
    data(:,3) = [];
    data(:,12)= [];

    featureSets = {};
 
    % featureSets contains the information related to the daset.
    % For each feature we store in a list all the admissible values we want
    % to consider during the exploration
    featureSets{1} = [0,3,9];
    featureSets{2} = [0,7];
    featureSets{3} = [0,3,9];
    featureSets{4} = [0,2,4,8];
    featureSets{5} = [0,1];
    featureSets{6} = [0,1];
    featureSets{7} = [0,1];
    featureSets{8} = [0,1];
    featureSets{9} = [0,1];
    featureSets{10} = [0,1];
    discretizedFeatureSets = discretizeSet(featureSets);

    dataCol = size(data,2);

    if resize
        data(:,3:dataCol) = discretizeFeature(featureSets,discretizedFeatureSets,data(:,3:dataCol));
        maxVal = max(data(:,1:2));
        data(:,1:2) = data(:,1:2)./maxVal;
    end

end